import libvirt as lv
import xml.etree.cElementTree as ET


class InvalidVMConfigError(Exception):
    def __str__(self):
        return 'Invalid VM config, perhaps some vital parameters haven\'t been set.'


class VMConfig:
    """The handy representation of VM configuration.

    Usage:
        >>> vmc = VMConfig()  # A new VMConfig with default parameters, and key parameters are None
        >>> vmc.set_image_path('./example.img')  # This has to be set
        >>> vmc.set_memory_size(1024)  # Size in MB
        >>> vmc.set_vm_type('kvm')  # VM type
        >>> vmc.to_xml()  # Convert to XML for libvirt
    """
    def __init__(self):
        self.name = None
        self.image_path = None
        self.cmdline = ''
        self.memory_size = 1024
        self.vm_type = None

    def __check(self):
        """Check if non-default parameters have been set.
            By non-default, I mean that it is None by default and have to be set before generation XML.
        """
        return all([self.name, self.image_path, self.vm_type])

    def to_xml(self):
        """Generate XML representation for libvirt.

        Raises:
            InvalidVMConfigError
        """
        if not self.__check():
            raise InvalidVMConfigError

        domain = ET.Element('domain')
        domain.set('type', 'kvm')

        name = ET.SubElement(domain, 'name')
        name.text = self.name

        os = ET.SubElement(domain, 'os')
        tp = ET.SubElement(os, 'type')
        tp.text = 'hvm'
        kernel = ET.SubElement(os, 'kernel')
        kernel.text = self.image_path
        cmdline = ET.SubElement(os, 'cmdline')
        cmdline.text = self.cmdline

        memory = ET.SubElement(domain, 'memory')
        memory.text = str(self.memory_size)

        return ET.tostring(domain).decode()


class VM:
    """Refer to a vm.

    All the public methods of this class will immediately
    affect virtual machine unless it raises an exception.

    Usage:
        >>> vmc = VMConfig()
        >>> # ...
        >>> vm = VM(vmc)  # Now there is a new cunik in cunik registry along with the vm instance
        >>> vm.start()
        >>> vm.stop()
        >>> vm.destroy()
    """
    def __init__(self, config: VMConfig):
        # TODO: should we define then start or just create?
        conn = lv.open('')  # TODO: set URI by vm type
        self.domain = conn.defineXML(config.to_xml())
        conn.close()

    def start(self):
        """Start the vm, may raise exception."""
        if self.domain.isActive():
            self.domain.resume()
        else:
            self.domain.create()

    def stop(self):
        self.domain.suspend()

    def destroy(self):
        try:
            self.domain.destroy()
        finally:
            self.domain.undefine()